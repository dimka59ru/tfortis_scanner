python setup.py build
pause
rem python setup.py bdist_msi
rem for /r %%e in (*.exe,*.dll) do upx "%%e" --best --compress-icons=0 --nrv2d --crp-ms=999999 -k
pause