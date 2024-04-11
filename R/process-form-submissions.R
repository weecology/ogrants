source(here::here("R", "form-data-functions.R"))

site_id <- get_site_id()
form_data <- get_form_data(site_id)
purrr::walk(form_data, process_form_data)
