import json
from flask import render_template, request, abort, redirect, url_for
from basketbot import db
from basketbot.datamodel import model as dm
from basketbot.forms import RetailSiteForm, ScrapingRuleForm


def create():
    form = RetailSiteForm(csrf_enabled=False)
    if form.validate_on_submit():
        rs = dm.RetailSite()
        if hasattr(form, 'countries'):
            del form.countries
        form.populate_obj(rs)
        db.session.add(rs)
        db.session.commit()
        # If we have scraping_data info then we need
        # to forward user on to a form for submitting 
        # a scraping rule
        if hasattr(form, 'scraping_rule') and (len(form.scraping_rule.data) > 0):
            scraping_form = ScrapingRuleForm()
            scraping_rule = json.loads(form.scraping_rule.data)
            scraping_form.retail_site.data = [rs]
            scraping_form.class_chain.data = json.dumps(scraping_rule.get('classChain'), indent=4)
            scraping_form.parent_elem.data = dm.DOMElem.query.filter(dm.DOMElem.bs_name==scraping_rule.get('parent_elem')).scalar() #scalar returns None if no rows found
            scraping_form.parent_id.data = scraping_rule.get('parent_id')
            return render_template(
                    'scraping/create.html',
                    form=scraping_form,
                    endpoint=url_for("frontend.scraping_rule_get_form")
                    )
        else:
            # Redirect to retail-site creation success page
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
