from dataclasses import dataclass, fields, asdict
from modules.utilities import get_core_settings
from modules.utilities import path_constructor
from modules.utilities import clean_string
from modules.utilities import ConfigLoader
from modules.utilities import base_path
from modules.plex import PlexApi
from modules.plex import ItemDetails, ItemID, ItemDate
plex = PlexApi()
configuration_data = ConfigLoader()
library_settings = configuration_data.settings
pmm_config = configuration_data.pmm_config

@dataclass
class InHistory:
    trakt_list_privacy: str = 'private'
    direction: str = 'desc'
    range: str = 'month'
    starting_year: int
    ending_year: int
    increment: int = 1
    metadata_save_folder: str = 'metadata/'
    collection_title: str = 'Released this {{range}} in history'
    collection: dict = {
        'visible_home': 'true',
        'visible_shared': 'true',
        'collection_order': 'custom',
        'sync_mode': 'sync',
        'poster_url': f'"https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Images/master/chart/This%20Month%20in%20History.jpg"'
    }


def run():
    allowed_instances = 1

    # Define default settings
    default_settings = InHistory()

    core_name = 'in_history'
    core_settings = get_core_settings(core_name, allowed_instances, default_settings)
    for library_name, core_settings_list in core_settings.items():
        # Library loop starts here

        library_slug = clean_string(library_name) # Get a clean library name for trakt
        print(f"Library slug: {library_slug}")

        print(f"Library: {library_name}")

        



        for settings in core_settings_list:

            library = plex.library(library_name)
            library_list = library.contents()
            if library.type == 'show':
                content_list = []
                for media in library_list:
                    show = plex.show(media.id.rating_key)
                    print(f"Calculating size for {show.title} - {show.size}")
                    content_list.append(ItemDetails(
                        title=show.title,
                        id=ItemID(
                            tmdb=show.id.tmdb,
                            imdb=show.id.imdb,
                            tvdb=show.id.tvdb
                        ),
                        date=ItemDate(
                            added_date=show.date.added_date,
                            year=show.date.year,
                            available_date=show.date.available_date
                        ),
                        size=show.size
                    ))
                    #content_list.append({'title': show.title, 'rating_key': show.id.rating_key, 'size': show.size})
                size_sorted_list = sorted(content_list, key=lambda x: x.size, reverse=True)

            if library.type == 'movie':
                # size is built in to the movie response data
                size_sorted_list = sorted(library_list, key=lambda x: x.size, reverse=True)


            
            
            # Instance of core per library starts here. Main operations of the Core should be in this indent.

            in_history = InHistory(**settings) # Unpack instance settings into dataclass.
            in_history.meta['trakt_list_url'] = f"https://trakt.tv/users/{pmm_config.trakt.username}/lists/sorted-by-size-{library_slug}"
            
            # Settings can be referenced by dataclass now
            print(in_history.starting_year)
            print(in_history.collection_title)
            for key, value in in_history.meta.items():
                print(f"\tmeta: {key} - {value}")

            # Or as a loop
            in_history_dict = asdict(in_history) # Turn dataclass instance into a dictionary item
            for item, value in in_history_dict.items(): # Iterate through dictionary
                if item == 'meta':
                    for keys, values in value.items():
                        print(f"{keys} - {values}")
                else:
                    print(f"{item} - {value}")




            size_in_range_list = [
                    item for item in size_sorted_list
                    if (
                        in_history.minimum <= item.size and
                        (in_history.maximum is None or item.size <= in_history.maximum)
                    )
                ]
            for v in size_in_range_list:
                print(f"Title: {v.title}, Size: {v.size} GB")

            # uploading to trakt or any functions this instance needs goes in this indent
            # for instance, i'd upload the size_in_range_list here and remove unused collections from plex here
            

        # path_constructor uses base path for file locations
        print(base_path())
        # define any files you need
        metadata_file = f"{library_slug}-in-history-metadata.yml"

        # get your save path
        metadata_file_path = path_constructor(in_history.metadata_save_folder, metadata_file)
        print(metadata_file_path)
        


"""

                logging.info(f"Extension setting found. Running 'In History' on {this_library}")
                
                in_history_settings = vars.Extensions(this_library).in_history.settings()
                
                pmm_in_history_folder = pmm_config_path_prefix + in_history_settings.save_folder
                if pmm_in_history_folder != '':
                    pmm_in_history_folder_exists = os.path.exists(pmm_in_history_folder)
                    if not pmm_in_history_folder_exists:
                        in_history_subfolder_path = f"config/{in_history_settings.save_folder}"
                        print(f"Sub-folder {in_history_subfolder_path} not found.")
                        print(f"Attempting to create.")
                        logging.info(f"Sub-folder {in_history_subfolder_path} not found.")
                        logging.info(f"Attempting to create.")
                        try:
                            os.makedirs(pmm_in_history_folder)
                            print(f"{in_history_subfolder_path} created successfully.")
                            logging.info(f"{in_history_subfolder_path} created successfully.")
                        except Exception as sf:
                            print(f"Exception: {str(sf)}")
                            logging.warning(f"Exception: {str(sf)}")
                in_history_range = in_history_settings.range
                trakt_user_name = vars.traktApi('me')
                library_clean_path = vars.cleanPath(in_history_settings.slug)
                collection_title = in_history_settings.collection_title
                in_history_meta = in_history_settings.meta
                try:
                    output_stream = StringIO()
                    yaml.dump(in_history_meta, output_stream)
                    in_history_meta_str = output_stream.getvalue()
                    output_stream.close()
                    in_history_meta_str = in_history_meta_str.replace("'","")
                    in_history_meta_str = in_history_meta_str.replace('{{range}}', in_history_range)
                    in_history_meta_str = in_history_meta_str.replace('{{Range}}', in_history_range.capitalize())
                except Exception as e:
                    print(f"An error occurred: {e}")


                in_history_file = f"{pmm_config_path_prefix}{in_history_settings.save_folder}{library_clean_path}-in-history.yml"
                in_history_file_exists = os.path.exists(in_history_file)

                if not in_history_file_exists:
                    try:
                        print(f"Creating {this_library} 'In History' metadata file..")
                        logging.info(f"Creating {this_library} 'In History' metadata file..")
                        create_in_history_file = open(in_history_file, "x")
                        create_in_history_file.write(in_history_meta_str)
                        create_in_history_file.close()
                        print(f"File created")
                        logging.info(f"File created")
                        in_history_file_location = f"config/{in_history_settings.save_folder}{library_clean_path}-in-history.yml"
                        print(f"{in_history_file_location}")
                        logging.info(f"{in_history_file_location}")
                    except Exception as e:
                        print(f"An error occurred: {e}")
                else:
                    print(f"Updating {this_library} 'In History' metadata file..")
                    logging.info(f"Updating {this_library} 'In History' metadata file..")
                    in_history_file_location = f"config/{in_history_settings.save_folder}{library_clean_path}-in-history.yml"
                    print(f"{in_history_file_location}")
                    logging.info(f"{in_history_file_location}")

                    with open(in_history_file, "r") as read_in_history_file:
                        loaded_in_history_yaml = yaml.load(read_in_history_file)

                        for key, value in loaded_in_history_yaml['collections'].items():
                            if key != collection_title:
                                print(f'''Collection for {this_library} has been changed from {key} ==> {collection_title}
Attempting to remove unused collection.''')
                                logging.info(f'''Collection for {this_library} has been changed from {key} ==> {collection_title}
Attempting to remove unused collection.''')
                                library_id = vars.plexGet(this_library)
                                old_collection_id = plex.collection.id(key, library_id)
                                delete_old_collection = plex.collection.delete(old_collection_id)
                                if delete_old_collection:
                                    print(f"Successfully removed old '{key}' collection.")
                                    logging.info(f"Successfully removed old '{key}' collection.")
                                else:
                                    print(f"Could not remove deprecated '{key}' collection.")
                                    logging.warning(f"Could not remove deprecated '{key}' collection.")

                    with open(in_history_file, "w") as write_in_history_file:
                        write_in_history_file.write(in_history_meta_str)
                        print('')
                        print(f'''{in_history_meta_str}''')
                        logging.info('')
                        logging.info(f'''{in_history_meta_str}''')


                month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
                
                
                if in_history_range == 'day':
                    today = datetime.now()
                    start_date = today
                    end_date = today

                if in_history_range == 'week':
                    today = datetime.now()
                    weekday_number = today.weekday()
                    first_weekday = today - timedelta(days=weekday_number)
                    days_till_last_weekday = 6 - weekday_number
                    last_weekday = today + timedelta(days=days_till_last_weekday)
                    start_date = first_weekday
                    end_date = last_weekday

                if in_history_range == 'month':
                    today = datetime.now()
                    first_day_of_month = today.replace(day=1)
                    if first_day_of_month.month == 12:
                        last_day_of_month = first_day_of_month.replace(day=31)
                    elif first_day_of_month.month < 12:
                        last_day_of_month = first_day_of_month.replace(month=first_day_of_month.month + 1) - timedelta(days=1)
                    start_date = first_day_of_month
                    end_date = last_day_of_month
                
                description_identifier = plex.library.type(this_library)
                if description_identifier == 'show':
                    description_type = 'Shows'
                    trakt_type = 'shows'
                if description_identifier == 'movie':
                    description_type = 'Movies'
                    trakt_type = 'movies'
                trakt_access = vars.traktApi('token')
                trakt_api = vars.traktApi('client')
                trakt_headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + trakt_access + '',
                    'trakt-api-version': '2',
                    'trakt-api-key': '' + trakt_api + ''
                    }
                trakt_list_url = f"https://api.trakt.tv/users/{trakt_user_name}/lists"
                trakt_list_url_post = f"https://api.trakt.tv/users/{trakt_user_name}/lists/in-history-{library_clean_path}"
                trakt_list_url_post_items = f"https://api.trakt.tv/users/{trakt_user_name}/lists/in-history-{library_clean_path}/items"
                trakt_list_data = f'''
{{
    "name": "In History {this_library}",
    "description": "{description_type} released this {in_history_range} in history.",
    "privacy": "{in_history_settings.trakt_list_privacy}",
    "display_numbers": true,
    "allow_comments": true,
    "sort_by": "rank",
    "sort_how": "asc"
}}
    '''
                print("Clearing " + this_library + " trakt list...")
                logging.info("Clearing " + this_library + " trakt list...")
                trakt_delete_list = requests.delete(trakt_list_url_post, headers=trakt_headers)
                if trakt_delete_list.status_code == 201 or 200 or 204:
                    print("List cleared")
                time.sleep(1.25)
                trakt_make_list = requests.post(trakt_list_url, headers=trakt_headers, data=trakt_list_data)
                if trakt_make_list.status_code == 201 or 200 or 204:
                    print("Initialization successful.")
                time.sleep(1.25)
                trakt_list_items = '''
{'''
                trakt_list_items += f'''
    "{trakt_type}": [
        '''
                print(f"Filtering ==> This '{in_history_range}' in history")
                logging.info(f'Filtering ==> This {in_history_range} in history')
                if in_history_settings.starting != 0:
                    print(f"From {in_history_settings.starting} to {in_history_settings.ending}")
                    logging.info(f"From {in_history_settings.starting} to {in_history_settings.ending}")
                if in_history_settings.starting == 0:
                    print(f"From earliest to {in_history_settings.ending}")
                    logging.info(f"From earliest to {in_history_settings.ending}")
                if in_history_settings.increment != 1:
                    print(f"{in_history_settings.increment} year increment")
                    logging.info(f"{in_history_settings.increment} year increment")
                if in_history_settings.increment == 1:
                    print(f"Using all years")
                    logging.info(f"Using all years")
                print(f'''
''')
                library_list = plex.library.list(this_library)
                library_list = sorted(library_list, key=lambda item: item.date)
                library_list_in_range = [item for item in library_list if date_within_range(item.date, start_date, end_date)]
                for entry in library_list_in_range:
                    title_in_range = plex.item.info(entry.ratingKey)
                    title_in_range_month = month_names[title_in_range.date.month - 1]

                    if title_in_range.details.tmdb and title_in_range.details.imdb and title_in_range.details.tvdb == 'Null':
                        continue
                    
                    if (in_history_settings.starting <= title_in_range.date.year <= in_history_settings.ending 
                        and (in_history_settings.ending - title_in_range.date.year) % in_history_settings.increment == 0
                        and title_in_range.date.year != today.year):
                        print(f"In History | + | {title_in_range.title} ({title_in_range_month} {title_in_range.date.day}, {title_in_range.date.year})")
                        logging.info(f"In History | + | {title_in_range.title} ({title_in_range_month} {title_in_range.date.day}, {title_in_range.date.year})")
                        trakt_list_items += f'''
    {{
    "ids": {{'''
                
                        if title_in_range.details.tmdb != 'Null':
                            trakt_list_items += f'''
        "tmdb": "{title_in_range.details.tmdb}",'''
                        if title_in_range.details.tvdb != 'Null':
                            trakt_list_items += f'''
        "tvdb": "{title_in_range.details.tvdb}",'''
                        if title_in_range.details.imdb != 'Null':
                            trakt_list_items += f'''
        "imdb": "{title_in_range.details.imdb}",'''
                        
                        trakt_list_items = trakt_list_items.rstrip(",")
                    
                        trakt_list_items += f'''
            }}
    }},'''
        
        
                trakt_list_items = trakt_list_items.rstrip(",")
                trakt_list_items += '''
]
}
'''
                
                post_items = requests.post(trakt_list_url_post_items, headers=trakt_headers, data=trakt_list_items)
                if post_items.status_code == 201:
                    print(f'''
    Successfully posted This {in_history_range} In History items for {this_library}''')
                    logging.info(f"Successfully posted This {in_history_range} In History items for {this_library}")


"""