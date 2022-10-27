# INFO Application

This is a Python Flask application, that serves the following information of the EC2 Instance it is deployed on:
- Region
- Availability Zone
- Private (internal) IP v4 address

## API

See [swagger.yml](openapi/swagger.yml) for the specification of the API. It can be imported to **PostMan** as well to test the deployed application.

The **Swagger UI** application is also available on the `{url}/ui` endpoints.