import click
from cpm.m01_detector.detector import BrowserDetector

@click.group()
def cli():
    """Chromium Profile Migrator (CPM) - Chuyển đổi dữ liệu trình duyệt an toàn."""
    pass

@cli.command()
def list():
    """Liệt kê các trình duyệt và profile hiện có trên máy."""
    click.echo("Đang quét hệ thống...")
    browsers = BrowserDetector.get_installed_browsers()
    
    if not browsers:
        click.echo("Không tìm thấy trình duyệt Chromium nào.")
        return
        
    for browser in browsers:
        if browser.is_installed:
            click.echo(f"\n[+] {browser.name} (ID: {browser.id})")
            for profile in browser.profiles:
                default_tag = " (Default)" if profile.is_default else ""
                click.echo(f"    - {profile.name}{default_tag}")

if __name__ == "__main__":
    cli()
