"""Main module for SERVERLESS Application"""

import os
import connexion
import yaml

with open('config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f.read())
    for k, v in config.items():
        if k not in os.environ:
            os.environ[k] = str(v)

AWS_REGION = os.environ['AWS_REGION']
QUEUE_URL = os.environ['QUEUE_URL']
TOPIC_ARN = os.environ['TOPIC_ARN']

options = {'awagger_ui': True}
app = connexion.FlaskApp(__name__,
                         specification_dir='openapi/',
                         options=options)
app.add_api('swagger.yml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
