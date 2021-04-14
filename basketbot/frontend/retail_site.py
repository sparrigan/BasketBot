from flask import render_template, request, abort, redirect
from basketbot import db
from basketbot.datamodel import model as dm
from basketbot.forms import RetailSiteForm


def create():
    form = RetailSiteForm(csrf_enabled=False)
    if form.validate_on_submit():
        print('here')
        print(request.data)
        print(request.form)
        fail
        rs = dm.RetailSite()
        if hasattr(form, 'countries'):
            del form.countries
        form.populate_obj(rs)
        db.session.add(rs)
        db.session.commit()
        return redirect('http://www.yahoo.com')
        # return redirect('http://www.google.com')
    return redirect('http://www.google.com')
        # return redirect(url_for('frontend.create_scraping_rule'))

# def create():
#     if request.method == "POST":
#         form = request.form
#         rs = dm.RetailSite(
#                 name = form.get('name'),
#                 url_protocol = form.get('url_protocol'),
#                 url_subdomain = form.get('url_subdomain'),
#                 url_domain = form.get('url_domain'),
#                 url_suffix = form.get('url_suffix'),
#                 )
#         rs.regions = [dm.Region.query.get(int(x)) for x in form.getlist('region')]
#         db.session.add(rs)
#         db.session.flush()
#         return render_template('retail_site/view.html', retail_site=rs)
