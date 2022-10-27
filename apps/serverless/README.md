# SERVERLESS Application

This is a Python Flask application, that handles images, the user can:

- Upload image that is saved to S3 and its metadata to a DynamoDB table
- Subscribe to notifications about image upload/delete events
- List/Get/Delete uploaded images

This application is a version of the **IMAGE** Application, but instead of a background process, it uses the lambda function to handle SQS events.

## API

See [swagger.yml](openapi/swagger.yml) for the specification of the API. It can be imported to **PostMan** as well to test the deployed application.

The **Swagger UI** application is also available on the `{url}/api/ui` endpoints.
