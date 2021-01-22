
PYTHON_PATH="lib/python3.7/site-packages"
python3 -m venv gcpenv
source gcpenv/bin/activate 
pip install --upgrade google-cloud-vision

deactivate
mkdir -p gcp_layer/python
cp -r gcpenv/$PYTHON_PATH/* gcp_layer/python/.
cd  gcp_layer
zip -r9 ../gcp_layer_package.zip *
cd ..

aws lambda publish-layer-version \
    --layer-name Google_cloud_Vision \
    --description "Google Cloud Vision Library" \
    --zip-file fileb://gcp_layer_package.zip \
    --compatible-runtimes python3.7
    
GCP_LAYER_VERSION_ARN=`aws lambda get-layer-version --version-number=1 --layer-name Google_cloud_Vision --query LayerVersionArn`

