import click
import configparser

from mdTistory import mdtistory

def get_tistory_conf(conf_path) :
    mdTistory_conf = {}
    mdTistory_conf['apikey'] = ''
    mdTistory_conf['blog_name'] = ''
    mdTistory_conf['base_folder'] = ''

    config = configparser.ConfigParser()
    config.read(conf_path)

    if config['tistory'] == None or len(config['tistory']) <= 0:
        return mdTistory_conf

    if config['tistory']['apikey'] != None and len(config['tistory']['apikey']) > 0 :
        mdTistory_conf['apikey'] = str(config['tistory']['apikey'])
    if config['tistory']['blog_name'] != None and len(config['tistory']['blog_name']) > 0 :
        mdTistory_conf['blog_name'] = str(config['tistory']['blog_name'])
    if config['tistory']['base_folder'] != None and len(config['tistory']['base_folder']) > 0 :
        mdTistory_conf['base_folder'] = str(config['tistory']['base_folder'])

    return mdTistory_conf


@click.group(chain=True, invoke_without_command=True)
@click.option('-c', '--config', type=click.Path('r'))
@click.pass_context
def cli(ctx, config):
    print('')
    ctx.ensure_object(dict)
    ctx.obj['CONFIG'] = config

@cli.command('read')
@click.option('-s', '--startid', default=-1)
@click.option('-e', '--endid', default=-1)
@click.pass_context
def mdTistory_read_post(ctx, startid, endid):
    click.echo('++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    click.echo('mdTistory CLI : read command')
    click.echo('  > config path is %s' % ctx.obj['CONFIG'])
    click.echo('  > startid is %d' % startid)
    click.echo('  > endid is %d' % endid)

    mdTistory_conf = get_tistory_conf(ctx.obj['CONFIG'])

    click.echo('  --- read config --- ')
    click.echo('    -> api key %s' % mdTistory_conf['apikey'])
    click.echo('    -> blog name %s' % mdTistory_conf['blog_name'])
    click.echo('    -> base folder %s' % mdTistory_conf['base_folder'])

    tistoryTool = mdtistory.TistoryTools(mdTistory_conf['apikey'])
    tistoryTool.get_category_folder_info(mdTistory_conf['blog_name'], mdTistory_conf['base_folder'])

    if startid > 0 and endid > 0 :
        for i in range(startid, endid):
            tistoryTool.read_post(i, mdTistory_conf['blog_name'], mdTistory_conf['base_folder'])
    elif startid > 0 and endid == -1 :
        tistoryTool.read_post(startid, mdTistory_conf['blog_name'], mdTistory_conf['base_folder'])
    else :
        click.echo('argument check fail.. ')

@cli.command('getinfo')
@click.pass_context
def mdTistory_getinfo(ctx):
    click.echo('++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    click.echo('mdTistory CLI : get info command')
    click.echo('  > config path is %s' % ctx.obj['CONFIG'])

    mdTistory_conf = get_tistory_conf(ctx.obj['CONFIG'])

    click.echo('  --- read config --- ')
    click.echo('    -> api key %s' % mdTistory_conf['apikey'])
    click.echo('    -> blog name %s' % mdTistory_conf['blog_name'])
    click.echo('    -> base folder %s' % mdTistory_conf['base_folder'])

    tistoryTool = mdtistory.TistoryTools(mdTistory_conf['apikey'])
    tistoryTool.get_category_folder_info(mdTistory_conf['blog_name'],mdTistory_conf['base_folder'])


@cli.command('scan')
@click.pass_context
def mdTistory_scan(ctx):
    click.echo('++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    click.echo('mdTistory CLI : get info command')
    click.echo('  > config path is %s' % ctx.obj['CONFIG'])

    mdTistory_conf = get_tistory_conf(ctx.obj['CONFIG'])

    click.echo('  --- read config --- ')
    click.echo('    -> api key %s' % mdTistory_conf['apikey'])
    click.echo('    -> blog name %s' % mdTistory_conf['blog_name'])
    click.echo('    -> base folder %s' % mdTistory_conf['base_folder'])

    tistoryTool = mdtistory.TistoryTools(mdTistory_conf['apikey'])
    tistoryTool.get_category_folder_info(mdTistory_conf['blog_name'],mdTistory_conf['base_folder'])
    check_post_files = tistoryTool.check_post_files(mdTistory_conf['blog_name'], mdTistory_conf['base_folder'])

    click.echo('..')
    click.echo('.. check new post')
    for new_post_fileinfo in check_post_files['new_post_fileinfo'] :
        click.echo(' -- new post target --')
        click.echo(new_post_fileinfo)
        print(new_post_fileinfo)
        tistoryTool.new_post_markdown_file(mdTistory_conf['blog_name'], new_post_fileinfo)

    click.echo('..')
    click.echo('.. check edit post')
    for update_post_fileinfo in check_post_files['update_post_fileinfo'] :
        click.echo(' -- edit post target --')
        print(update_post_fileinfo)
        tistoryTool.edit_post_markdown_file(mdTistory_conf['blog_name'], update_post_fileinfo)

if __name__ == '__main__':
    cli()