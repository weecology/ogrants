netlify_config <- function(token = NULL)
{
    if (is.null(token))
    {
        token <- Sys.getenv("netlify_token")
    }
    if (token == "")
    {
        stop("could not get netlify personal access token")
    }
    httr::add_headers(Authorization = paste("Bearer", token))
}

get_site_id <- function(site = "https://www.ogrants.org", 
                        url = "https://api.netlify.com/api/v1/sites")
{
    resp <- httr::GET(url = url, config = netlify_config())
    sites <- httr::content(resp)
    
    urls <- purrr::map_chr(sites, "url")
    idx <- match(site, urls)
    if (is.na(idx))
    {
        stop("did not find ", site, " among netlify sites.") 
    }
    sites[[idx]]$site_id
}

get_form_data <- function(site_id)
{
    url <- paste0("https://api.netlify.com/api/v1/sites/", site_id, "/submissions")
    resp <- httr::GET(url = url, config = netlify_config())
    httr::content(resp)
}

process_form_data <- function(dat)
{
    dat <- dat$data
    grant_file <- create_grant_filename(dat$author, dat$year)
    grant_data <- create_grant_data(dat, grant_file)
    write_yaml_file(grant_data, grant_file, 
                    fix_link_name = TRUE)
    
    author_data <- create_author_data(dat)
    author_file <- create_author_filename(dat$author)
    if (!file.exists(author_file))
    {
        write_yaml_file(author_data, author_file)
    }
}

extract_name <- function(author)
{
    name_pattern_begin <- "^[\\s,]*([^\\s,]+)"
    name_pattern_end <-  "([^\\s,]+)[\\s,]*$"
    if (stringr::str_detect(author, ",") || stringr::str_detect(author, " and "))
    {
        first_name <- tolower(stringr::str_extract(author, name_pattern_begin, group = 1))
        remainder <- stringr::str_remove(author, name_pattern_begin)
        last_name <- tolower(stringr::str_extract(remainder, name_pattern_begin, group = 1))
    } else {
        first_name <- tolower(stringr::str_extract(author, name_pattern_begin, group = 1))
        last_name <- tolower(stringr::str_extract(author, name_pattern_end, group = 1))
    }    
    paste0(last_name, "_", first_name)
}

create_grant_filename <- function(author, year)
{
    name <- extract_name(author)
    grant_file <- here::here("_grants", 
                             paste0(name, "_", year, ".md"))
    counter <- 1
    while (file.exists(grant_file))
    {
        if (is.na(letters[counter]))
        {
            stop("exceeded max number of grant files for ", 
                 name, "_", year)
        }
        grant_file <- here::here("_grants", 
                                 paste0(name, "_", 
                                        year, letters[counter], ".md"))
        counter <- counter + 1
    }
    grant_file
}

create_grant_data <- function(dat, grant_file)
{
    grant_data <- data.frame(layout = "grant", 
                             title = dat$title, 
                             author = dat$author, 
                             ORCID = dat$ORCID, 
                             year = dat$year, 
                             institution = dat$institution, 
                             link = dat$link, 
                             funder = dat$funder, 
                             program = dat$program, 
                             discipline = dat$discipline, 
                             status = tolower(dat$status))
    
    if (grant_data$ORCID == "") # no ORCID
    {
        grant_data$ORCID <- NULL
    }
    
    if (grant_data$program == "") # no program
    {
        grant_data$program <- NULL
    }
    
    if (grant_data$link == "") # no link to proposal
    {
        if (is.null(dat$file) || dat$file$filename == "") # use uploaded file
        {
            stop("no link to proposal found, and no proposal attached")
        }
        
        destfile <- here::here("proposals", gsub("\\.md$", "\\.pdf", basename(grant_file)))
        if (file.exists(destfile))
        {
            stop(destfile, " already exists.")
        }
        
        result <- download.file(dat$file$url, destfile)
        message("Downloaded ", basename(destfile))
        if (result != 0)
        {
            stop("an error occurred while trying to download the file")
        }
        
        grant_data$link <- paste0("https://www.ogrants.org/proposals/", 
                                  basename(destfile))
        grant_data$link_name <- "Proposal"
    }
    
    grant_data
}

write_yaml_file <- function(yaml_data, yaml_file, silent = FALSE, 
                            fix_link_name = FALSE)
{
    to_write <- paste0("---\n", 
                       yaml::as.yaml(yaml_data), 
                       "---\n")
    if (fix_link_name)
    {
        to_write <- gsub("link_name: Proposal", 
                         "link_name: \\[Proposal\\]", 
                         to_write)
    }
    writeLines(to_write, yaml_file)
    if (!silent)
    {
        message("Wrote ", basename(yaml_file))
    }
}

create_author_data <- function(dat)
{
    author_data <- data.frame(
        name = dat$author, 
        institution = dat$institution, 
        website = dat$website, 
        twitter = dat$twitter
    )
}

create_author_filename <- function(author)
{
    name <- extract_name(author)
    here::here("_authors", 
               paste0(name, ".md"))
}