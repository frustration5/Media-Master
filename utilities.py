import logger

media_logger = logger.logging.getLogger(__name__)


def format_for_html(search_input) -> str:
    if " " in search_input:
        output = search_input.replace(" ", "%20")
        media_logger.info(f"Formatting title for HTML: Replaced '{search_input}' with '{output}'")
        return output
    else:
        media_logger.info(f"Formatting title for HTML: Nothing to replace...")
        return search_input
