# fpi
## Prepare git credentials

```shell
kubectl --namespace argo create secret generic gh-wostal \
  --from-literal=username=$GITHUB_USERNAME \
  --from-literal=token=$GITHUB_TOKEN \
  --from-literal=email=$GITHUB_EMAIL \
  --output json \
  --dry-run=client | \
  kubeseal --format yaml \
  --controller-name=sealed-secrets \
  --controller-namespace=sealed-secrets | \
  tee ./gh-wostal-secret.yaml
```