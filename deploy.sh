# Settings in .env have prio
if [ -f ./configuration/settings.ini ]; then
  set -o allexport
  source ./configuration/settings.ini
  set +o allexport
fi


echo "Using Domain: $DOMAIN"

kubectl apply -f ./yaml/namespace.yaml
cat ./yaml/deployment.yaml | sed "s~<DOMAIN>~$DOMAIN~g" | kubectl apply -f -
kubectl apply -f ./yaml/service.yaml

cat ./yaml/istio-authpolicy.yaml | sed "s~<DOMAIN>~$DOMAIN~g" | kubectl apply -f -
cat ./yaml/istio-virtualservice.yaml | sed "s~<DOMAIN>~$DOMAIN~g" | kubectl apply -f -

