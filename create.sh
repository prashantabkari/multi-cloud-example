
PYTHON_PATH="python/lib/python3.7/site-packages"
python3 -m venv gcpenv
pip install --upgrade google-cloud-vision

mkdir -p gcp_layer/python
cp gcpenv/$PYTHON_PATH/* gcp_layer/python/
cd  gcp_layer
zip -r9 ../gcp_layer_package.zip *
cd ..

aws lambda publish-layer-version \
    --layer-name Google_cloud_Vision \
    --description "Google Cloud Vision Library" \
    --zip-file fileb://gcp_layer_package.zip \
    --compatible-runtimes python3.7
    
GCP_LAYER_VERSION_ARN=`aws lambda get-layer-version --layer-name Google_cloud_Vision --query LayerVersionArn`

