from app import create_app
import conf

application = create_app('config.DevelopmentConfig')

if __name__ == '__main__':
  application.run(host='0.0.0.0', port=4040)