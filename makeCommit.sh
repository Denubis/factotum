git add -A
git commit -a
git push
python3 setup.py clean sdist bdist_egg bdist_wheel upload --identity="Brian Ballsun-Stanton" --sign

