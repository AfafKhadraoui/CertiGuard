# Example workflow

```bash
certiguard gen-keys --private-key keys/private.pem --public-key keys/public.pem
certiguard gen-request --state-dir runtime/clientA --out runtime/clientA/clientA.cgreq.json
certiguard issue-license --request runtime/clientA/clientA.cgreq.json --private-key keys/private.pem --out runtime/clientA/license.certiguard.json --issued-to ACME --max-users 50 --modules hr,invoicing --valid-days 365 --exe-hash deadbeef
certiguard verify --state-dir runtime/clientA --license runtime/clientA/license.certiguard.json --public-key keys/public.pem --heartbeat-key local-secret --features 30,9,3,42
certiguard renewal-export --state-dir runtime/clientA --out runtime/clientA/renewal_request.json
```

