import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="sale_report", methods=["GET"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    domain = req.params.get('domain')
    if not domain:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            domain = req_body.get('domain')
    if domain:
        #process the domain and generate a sale report
        return func.HttpResponse(f"Sale report generated for domain: {domain}")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a domain in the query string or in the request body for a personalized response.",
             status_code=200
        )