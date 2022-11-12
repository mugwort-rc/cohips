# Cloud Optimized HiPS

## hips2cotiff.py

```
# prepare images
mkdir -p color-Rp-G-Bp-flux-map/Norder0/Dir0
pushd color-Rp-G-Bp-flux-map/Norder0/Dir0
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix0.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix1.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix2.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix3.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix4.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix5.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix6.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix7.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix8.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix9.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix10.jpg
wget http://alasky.cds.unistra.fr/ancillary/GaiaDR3/color-Rp-G-Bp-flux-map/Norder0/Dir0/Npix11.jpg
popd
# generate Cloud Optimized HiPS
python hips2cotiff.py color-Rp-G-Bp-flux-map 0
# 0.tif
```
