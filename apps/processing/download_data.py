from tqdm import tqdm
import urllib.request
import zipfile
from glob import glob


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


if len(glob("data/wc21prec/*.tif")) == 0:
    download_url('https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_30s_prec.zip',
                 "data/wc21prec.zip")
    with zipfile.ZipFile("data/wc21prec.zip", 'r') as zip_ref:
        zip_ref.extractall("data/wc21prec")

precip_files = glob("data/wc21prec/*.tif")
indiv_calc_precip = False