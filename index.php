<?php
    $response = 'UPD_LATEST_VERSION';
    $cur_ver = "2.00";

    if ($_REQUEST['ea_name']=="Expert") {
        if ($_REQUEST['ea_version']!="$cur_ver") $response = "UPD_OUTDATED_VERSION|$cur_ver|https://trendchaser.ru/checkupdates/Expert.ex4";
    }

    $response = iconv("utf-8","windows-1251",$response);
    echo $response;
?>