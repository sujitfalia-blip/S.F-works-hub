from services.create_work_service import create_work

@work.route('/create', methods=['POST'])
def create():

    return create_work(request.form)
  
