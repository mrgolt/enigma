<?php
    $response = 'UPD_LATEST_VERSION';
    $cur_ver = "2.0.0";

    if ($_REQUEST['ea_name']=="Enigma") {
        if ($_REQUEST['ea_version']!="$cur_ver") $response = "UPD_OUTDATED_VERSION|$cur_ver|http://trendchaser.ru/enigma.ex4";
    }
    else
    {
    $response = "";
    }

    $response = iconv("utf-8","windows-1251",$response);
    echo $response;
?>