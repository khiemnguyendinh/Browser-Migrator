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

@cli.command()
@click.option('--source', required=True, help='ID của trình duyệt nguồn (vd: chrome, edge)')
@click.option('--target', required=True, help='ID của trình duyệt đích (vd: edge, brave)')
def migrate(source, target):
    """Thực hiện migrate dữ liệu giữa 2 trình duyệt."""
    from cpm.orchestrator import MigrationOrchestrator
    
    browsers = BrowserDetector.get_installed_browsers()
    source_browser = next((b for b in browsers if b.id == source and b.is_installed), None)
    target_browser = next((b for b in browsers if b.id == target and b.is_installed), None)
    
    if not source_browser:
        click.echo(f"Lỗi: Không tìm thấy trình duyệt nguồn '{source}'.")
        return
    if not target_browser:
        click.echo(f"Lỗi: Không tìm thấy trình duyệt đích '{target}'.")
        return
        
    source_profile = next((p for p in source_browser.profiles if p.is_default), None)
    target_profile = next((p for p in target_browser.profiles if p.is_default), None)
    
    if not source_profile or not target_profile:
        click.echo("Lỗi: Không tìm thấy profile mặc định.")
        return
        
    click.echo(f"Bắt đầu migrate từ {source_browser.name} sang {target_browser.name}...")
    orchestrator = MigrationOrchestrator()
    success = orchestrator.migrate(
        source, source_profile.path, 
        target, target_profile.path
    )
    
    if success:
        click.echo("Migrate thành công! Vui lòng khởi động lại trình duyệt đích.")
    else:
        click.echo("Migrate thất bại. Vui lòng kiểm tra log.")

if __name__ == "__main__":
    cli()
