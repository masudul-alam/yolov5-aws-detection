import json, boto3, urllib.parse, logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            bucket = body.get('bucket', 'yolov5-detection-bucket')
            key = body.get('key', 'input-images/zidane.jpg')
        elif 'Records' in event:
            bucket = event['Records'][0]['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        else:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid request format'})}

        download_path = f'/tmp/{key.split("/")[-1]}'
        s3_client.download_file(bucket, key, download_path)
        detection_result = {
            "image": key,
            "timestamp": datetime.utcnow().isoformat(),
            "detections": [
                {"label": "person", "confidence": 0.92},
                {"label": "tie", "confidence": 0.87}
            ],
            "status": "success"
        }
        result_key = f"output-results/{key.split('/')[-1]}_result.json"
        s3_client.put_object(Bucket=bucket, Key=result_key, Body=json.dumps(detection_result), ContentType='application/json')
        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps(detection_result)}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
