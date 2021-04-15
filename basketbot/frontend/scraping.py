from flask import render_template, request, url_for
from basketbot import db
from basketbot.datamodel import model as dm
from basketbot.forms import ScrapingRuleForm, RetailSiteForm
from basketbot.util import decompose_url
from basketbot.schemas import CountryRegions

def get_form():
    """
    This endpoint returns the correct form for a given retail site URL.
    If the site is not known then a create-site form is returned.
    If the site is known then a create-scraping-rule form is returned.
    """
    site_url = request.args.get('url', default=None, type=str)
    site = dm.RetailSite.get_site_from_url(site_url)
    if site is None:
        form = RetailSiteForm(csrf_enabled=False)
        deconstructed_url = decompose_url(site_url)
        countries = CountryRegions(many=True).dump(dm.Country.query.all())
        country_region_dict = {country.pop('country_id'): country for country in countries}
        return render_template(
                'retail_site/create.html',
                form=form,
                endpoint=url_for('frontend.retail_site_create'),
                durl=deconstructed_url,
                country_region_dict = country_region_dict 
                )
    else:
        form = ScrapingRuleForm()
        return render_template('scraping/create.html', form=form)
