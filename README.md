# setup

## setup AWS CLI environment using Docker 
1. Build docker image from tools 
```
cd tools
docker build --tag=daws .
```

2. dowload the appropriate accessKeys.csv file and put it in the current dir.

3. perform aws commands using the local shell script
```
aws.sh iam get-user
```
## Create a Thing
*NB- scripts imported from [Amazon FreeRTOS](https://github.com/aws/amazon-freertos) and unchanged. 

1. Edit configure.json to set `thing_name`
2. Inspect `policy_document.templ` for appropriateness and modify if desired
3. Create a new thing, certificate, and policy
```
cd tools
python3 ./SetupAWS.py prereq
```
*NB- this can be undone with
```
python3 ./SetupAWS.py delete_prereq
```
4. Copy the certificates to a certs dir
```
mkdir ../certs
THINGNAME=$(cat configure.json | jq ".thing_name" | sed -e 's/^"//' -e 's/"$//')
cp ${THINGNAME}*_file ../certs/
```

## Add Thing to Greengrass group
1. log in to console
2. navigate to IOT / Greengrass / Groups / <group name> / Devices
3. Add device / existing thing

## set endpoint address and root cert
1. Using AWS CLI
```
aws iot describe-endpoint --endpoint-type iot:data-ats | jq '.endpointAddress' 
```
2. download the appropriate root CA 
```
curl https://www.amazontrust.com/repository/AmazonRootCA1.pem >AmazonRootCA1.pem
```



## modify the source
the AWS IOT Device Python SDK is incorporated as a git submodule. To get python to find this module, we need to make a symlink to the actual code folder.  Do this with
```
ln -s aws-iot-device-sdk-python/AWSIoTPythonSDK ./AWSIoTPythonSDK
```
*NB-* can't just use a path import due to the dashs, which confuses python.  

also using the braviarc library as a submodule, which relies on requests, so install that with pip
```
pip3 install requests
```

Install the git submodules to PIP
```
pip3 install ./aws-iot-device-sdk-python
pip3 install git+https://github.com/aparraga/braviarc.git
```



# references
The Bravia API is described [here](https://pro-bravia.sony.net/develop/integrate/rest-api/spec/getting-started/)

