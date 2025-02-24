import datetime
import json
import dns.resolver
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib.parse import urljoin
from xportal.utils import RestHelper, get_endpoint
from xportal.icm import IncidentCreationResult
import asyncio
import uuid
import time

class HostSSLContext(ssl.SSLContext):
    def __new__(cls, hostname):
        instance = super(HostSSLContext, cls).__new__(cls, ssl.PROTOCOL_TLS_CLIENT)
        instance._hostname = hostname
        return instance

    def wrap_socket(self, *args, **kwargs):
        kwargs['server_hostname'] = self._hostname
        return super(HostSSLContext, self).wrap_socket(*args, **kwargs)

class HostHeaderSSLAdapter(HTTPAdapter):
    def send(self, request, **kwargs):
        hostname = request.headers.get('Host', None)

        if hostname:
            context = HostSSLContext(hostname)
            self.init_poolmanager(self._pool_connections, self._pool_maxsize, block=self._pool_block, ssl_context=context)

        connection_pool_kwargs = self.poolmanager.connection_pool_kw

        if hostname:
            connection_pool_kwargs['assert_hostname'] = hostname
        elif 'assert_hostname' in connection_pool_kwargs:
            connection_pool_kwargs.pop('assert_hostname', None)

        return super(HostHeaderSSLAdapter, self).send(request, **kwargs)

async def create_incident(title, summary):
    now = datetime.datetime.utcnow()
    body = {
        "Status": "Active",
        "Title": title,
        "Severity": 2,
        "RoutingId": "mdm://XStore/Triage",
        "CorrelationId": f"{account}{now.strftime('%Y%m%d')}"
    }
    if len(summary):
        body["Summary"] = "<br>".join(summary)
    result = await RestHelper.fetch_post(
        urljoin(get_endpoint(), "/api/v1/Icm/CreateIncident"),
        json.dumps(body, default=str),
    )
    return IncidentCreationResult(result)

def get_cname(qname, resolver=dns.resolver.Resolver()):
    try:
        cname_records = [rdata.target for rdata in resolver.resolve(qname, "CNAME")]
        if len(cname_records) != 0:
            return cname_records[0].to_text()
    except dns.resolver.NoAnswer:
        return None

def resolve_cname_recursively(domain, resolver=dns.resolver.Resolver()):
    cname = get_cname(domain, resolver)
    while cname:
        print(cname)
        next_cname = get_cname(cname, resolver)
        if not next_cname:
            break
        cname = next_cname
    return cname

async def probe_accounts(accounts, time_to_probe_in_seconds):
    session = requests.Session()
    session.mount('https://', HostHeaderSSLAdapter())

    start_time = time.perf_counter()
    cnames = dict()
    ingest_data = []
    total_probe = 0
    failed_probe = 0
    incident_id = None

    while time.perf_counter() - start_time < time_to_probe_in_seconds:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        request_id = uuid.UUID(int=0)
        status_code = -1
        error_detail = ""
        per_request_start_time = time.perf_counter()
        url = ""
        final_cname = ""
        ip_address = ""

        for account in accounts:
            try:
                final_cname = resolve_cname_recursively(account)
                ip_address = get_a(final_cname)
                print(f"Final CNAME: {final_cname}, IP address: {ip_address}")
                url = f"https://{ip_address}/bdprobe?"

                if final_cname not in cnames:
                    cnames[final_cname] = {ip_address: 1}
                else:
                    if ip_address not in cnames[final_cname]:
                        cnames[final_cname][ip_address] = 1
                    else:
                        cnames[final_cname][ip_address] += 1

                response = session.head(url, headers={"Connection": "close", "Host": account}, timeout=10)
                request_id = response.headers.get("x-ms-request-id", request_id)
                status_code = response.status_code
                print(f"HEAD request to {url} succeeded with status code {response.status_code}, {request_id}")

            except Exception as e:
                print(f"HEAD request failed: {e}")
                failed_probe += 1
                error_detail = str(e)

            total_probe += 1
            per_request_elapsed_time = time.perf_counter() - per_request_start_time
            ingest_data.append([timestamp, account, url, request_id, status_code, per_request_elapsed_time, error_detail, final_cname, ip_address])

            if not incident_id and failed_probe >= 10:
                incident = await create_incident(f"Connectivity issue with account {account}", ingest_data)
                incident_id = incident.incident_id
                print(f"Created incident {incident_id}")

            remaining_time = 1 - per_request_elapsed_time
            if remaining_time > 0:
                time.sleep(remaining_time)

    print(cnames)