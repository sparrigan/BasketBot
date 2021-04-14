$(function() {
    // Get initial set of active countries
    var activeCountries = $('#site-country-options').val();
    $('#site-country-options').on('change', function() {
        // Clear existing region options
        var newCountries = $('#site-country-options').val()
        // Remove region options if a country has been unchecked 
        console.log(activeCountries);
        console.log(newCountries);
        activeCountries.filter(country => !newCountries.includes(country))
            .forEach(country => {
                countryRegions[country]['regions']
                    .forEach(region=>{
                        // $('#region-'+region.region_id).remove()
                        $('#site-region-options option[value='+region.region_id+']').remove()
                    })
            });
        // Add in new region options if a new country was checked
        newCountries.filter(country => !activeCountries.includes(country))
            .forEach(country => {
                countryRegions[country]['regions']
                    .forEach(region => {
                        $('#site-region-options').append(
                            // jQuery('<option/>', {id: 'region-'+region.region_id, text: region.name, 'data-regionid': region.region_id})
                            jQuery('<option/>', {value: region.region_id, text: region.name})//, 'data-regionid': region.region_id})
                        )
                    })
            });
        // Update list of currently active countries
        activeCountries = newCountries;
    });
    // Listen for form submit and update region IDs
    $('#create-site-form').submit(function() {
        // This gets all the selected region values
        console.log($('#site-region-options').val());
        // $("#site-region-options > option")
        //         .each(function(i) {
        //             $(this).val($(this).data("regionid"))
        //         });
        return true;
    });
});
