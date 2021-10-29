# Script for updating all the .po files, and .mo files
# This keeps locales for docker and the module separate

function update_or_copy() {
    locales=$1
    for lang in $locales/*; do
        if [[ -d $lang ]]; then
            po_file=$lang/LC_MESSAGES/genshinhelper.po
            mo_file=$lang/LC_MESSAGES/genshinhelper.mo
            if [[ -f $po_file ]]; then
                # If the po file already exists, merge it
                msgmerge --update $po_file $locales/genshinhelper.pot
            else
                # Else copy the template file
                cp $locales/genshinhelper.pot $po_file
            fi
            msgfmt -o $mo_file $po_file
        fi
    done
}

# mkdir -p locale genshinhelper/locale
mkdir -p genshinhelper/locale
# xgettext -o locale/genshinhelper.pot *.py --from-code=UTF-8
# xgettext -o genshinhelper/locale/genshinhelper.pot genshinhelper/*.py genshinhelper/*/*.py --from-code=UTF-8
xgettext -o genshinhelper/locale/genshinhelper.pot genshinhelper/*.py --from-code=UTF-8

# update_or_copy "locale"
update_or_copy "genshinhelper/locale"
