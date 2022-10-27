"""Main module for the INFO app"""

import connexion

options = {'awagger_ui': True}
app = connexion.FlaskApp(__name__,
                         specification_dir='openapi/',
                         options=options)
app.add_api('swagger.yml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
