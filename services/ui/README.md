# services/ui (M1)

Web interface: React and TypeScript, built with Vite, served by unprivileged nginx. **Walking skeleton** (P01.03):
one form and its result. No login, history or live progress yet.

## API address at run time
The app calls only `/api/...` on its own origin. nginx forwards `/api/` to `API_URL`, read when the container
starts, so the same image runs against any API address. No address is built into the bundle.

| Setting | Value |
|---|---|
| Port | 8080 |
| `API_URL` | required; the gateway's address without a trailing slash, for example `http://gateway:8000` |
| Probes | `/health`, `/ready` |
| User | 101 |

nginx stops at start-up if `API_URL` is missing or its host name does not resolve.

```sh
docker build -t scd-ui services/ui
docker run --rm -p 8080:8080 -e API_URL=http://gateway:8000 --network <network with the gateway> scd-ui
```

## Development
```sh
npm ci
API_URL=http://127.0.0.1:8000 npm run dev   # with the gateway running: python -m scd_gateway.app
npm test && npm run lint && npm run typecheck
```
