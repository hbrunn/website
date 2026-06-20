import check_vendor_libs
import io
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import TestCase, mock


@contextmanager
def _mock_repo(*repo_files):
    with (
            mock.patch("check_vendor_libs.HTTPSConnection") as mock_connection_class,
            mock.patch("check_vendor_libs.Path.home") as mock_path_home,
            tempfile.TemporaryDirectory() as tmp_dir
    ):
        tar_bytes = io.BytesIO()
        repo_tarfile = tarfile.open(fileobj=tar_bytes, mode="w:gz")

        def add_tar(name, file_content=None, **kwargs):
            tar_info = tarfile.TarInfo(name=name)
            for key, value in kwargs.items():
                setattr(tar_info, key, value)
            fileobj = None
            if file_content:
                fileobj = io.BytesIO(file_content)
                tar_info.size = len(file_content)
            repo_tarfile.addfile(tar_info, fileobj=fileobj)

        for name, properties in repo_files:
            add_tar(name, **properties)
        repo_tarfile.close()
        tar_bytes.seek(0)

        mock_connection = mock.Mock()
        mock_connection_class.return_value = mock_connection
        mock_response = mock.Mock(status=200)
        mock_response.headers = {'content-type': 'application/x-gzip'}
        mock_response.read = mock.Mock(side_effect=tar_bytes.read)
        mock_connection.getresponse = mock.Mock(return_value=mock_response)

        mock_path_home.return_value = Path(tmp_dir)

        yield


class TestCheckVendorLibs(TestCase):
    def test_all_good(self):
        with _mock_repo(
            ("archive_dir", dict(type=tarfile.DIRTYPE)),
            ("archive_dir/vendorfile", dict(type=tarfile.REGTYPE, file_content=b'content of vendorfile\n')),
            ("archive_dir/subdir1", dict(type=tarfile.DIRTYPE)),
            ("archive_dir/subdir1/vendorfile-subdir1", dict(type=tarfile.REGTYPE, file_content=b'content of vendorfile-subdir1\n')),
            ("archive_dir/subdir1/subdir1-1", dict(type=tarfile.DIRTYPE)),
            ("archive_dir/subdir1/subdir1-1/vendorfile-subdir1-1", dict(type=tarfile.REGTYPE, file_content=b'content of vendorfile-subdir1-1\n')),
        ), self.assertNoLogs('check-vendor-libs'):
            result = check_vendor_libs.check_paths(['tests/test_repos/repo/vendor'])
        self.assertTrue(result)

    def test_content_differs(self):
        with _mock_repo(
            ("archive_dir", dict(type=tarfile.DIRTYPE)),
            ("archive_dir/subdir1", dict(type=tarfile.DIRTYPE)),
            ("archive_dir/subdir1/vendorfile-subdir1", dict(type=tarfile.REGTYPE, file_content=b'different')),
            ), self.assertLogs('check-vendor-libs') as logs:
            result = check_vendor_libs.check_paths(['tests/test_repos/repo/vendor'])
        self.assertFalse(result)
        self.assertTrue(any('vendorfile-subdir1 differs' in line for line in logs.output))
        self.assertTrue(any('vendorfile-subdir1-1 does not' in line for line in logs.output))
