for file in files/* 
do
    if [ -f "$file" ]; then
        echo "$file"
        python ./../../LICM.py "$file" > ./tmp/output.c
        file_name=$(basename "$file")
        if [ -f ./valid/"$file_name" ];then
            diff -w ./tmp/output.c ./valid/"$file_name"
            echo "OK"
        else
            echo "No valid file to compare"
        fi
    fi
done
