RELEASE=`date +%s`
RELEASE_DIR="/tmp/youvj.com-$RELEASE"
mkdir $RELEASE_DIR
cp *.sh $RELEASE_DIR
cp *.py $RELEASE_DIR
cp -r static $RELEASE_DIR
cp -r templates $RELEASE_DIR
mv $RELEASE_DIR/config-live.py $RELEASE_DIR/config.py
cd /tmp
tar -cvzf /tmp/youvj-$RELEASE.tgz youvj.com-$RELEASE
rm -rf $RELEASE_DIR
scp /tmp/youvj-$RELEASE.tgz youvj.com:/var/releases/youvj.com-$RELEASE.tgz
ssh youvj.com "cd /var/releases; tar -xvzf /var/releases/youvj.com-$RELEASE.tgz; rm /var/www/youvj.com; ln -fs /var/releases/youvj.com-$RELEASE /var/www/youvj.com; cd /var/www/youvj.com; sudo ./cycle.sh"