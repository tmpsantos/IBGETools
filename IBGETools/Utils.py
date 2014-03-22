import os
import stat

from jinja2 import Environment, FileSystemLoader


def _GetJinjaTemplate(name):
    this_directory = os.path.dirname(os.path.realpath(__file__))
    templates_directory = os.path.join(this_directory, "templates")
    environment = Environment(loader=FileSystemLoader(templates_directory))

    return environment.get_template(name)


def KMLFileWriter(kml, id, region):
    def ItemList():
        for ibge_map in region.GetRectangles():
            basename = os.path.splitext(os.path.basename(ibge_map.GetPath()))[0]
            href = "%s_%s.png" % (id, basename)

            item = {"href": href,
                    "north": ibge_map.GetTop(),
                    "south": ibge_map.GetBottom(),
                    "east": ibge_map.GetRight(),
                    "west": ibge_map.GetLeft()}

            yield item

    template = _GetJinjaTemplate("kml.jinja")
    kml.write(template.render(item_list=ItemList()))


def TileScriptFileWriter(script, id, region_id, should_upload, region):
    def ItemList():
        for ibge_map in region.GetRectangles():
            basename = os.path.splitext(os.path.basename(ibge_map.GetPath()))[0]

            item = {"name": "%s_%s" % (id, basename),
                    "vrt_name": "%s_%s_%s" % (id, region_id, basename),
                    "north": ibge_map.GetTop(),
                    "south": ibge_map.GetBottom(),
                    "east": ibge_map.GetRight(),
                    "west": ibge_map.GetLeft()}

            yield item

    config = None
    if should_upload:
        config = "%s/.tilemill/config.json" % os.getenv("HOME")

    data = {"id": "%s_%s" % (id, region_id),
            "config": config,
            "current_path": os.getcwd(),
            "north": region.GetTop(),
            "south": region.GetBottom(),
            "east": region.GetRight(),
            "west": region.GetLeft()}

    template = _GetJinjaTemplate("script.jinja")
    script.write(template.render(item_list=ItemList(), data=data))

    script_stat = os.fstat(script.fileno())
    os.fchmod(script.fileno(), script_stat.st_mode | stat.S_IEXEC)
