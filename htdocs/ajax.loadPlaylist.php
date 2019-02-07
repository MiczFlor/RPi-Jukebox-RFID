<?php
include("inc.playerStatus.php");

print '
<table style="width: 100%; border-collapse: collapse; border-top: 1px solid #444;">';
$i=0;
foreach($plFile[1] AS $file) {
    print '
    <tr style="border-bottom: 1px solid #444;">
        <td style="width: 70px!important; border-collapse: collapse;">
            <a href="?playpos='.$i.'" class="btn btn-success" style="margin: 3px!important;"><i class="mdi mdi-play" aria-hidden="true"></i></a>
        </td>
        <td style="border-collapse: collapse;">';
    if(trim($plTitle['1'][$i]) != "") {
        print '
            <strong>'.$plTitle['1'][$i].'</strong>';
    } else {
        print '
            <strong>'.basename($file).'</strong>';
    }
    print '
        <br><i>'.str_replace(";", " and ", $plArtist['1'][$i]).'</i>';
        if (empty($plAlbum['1'][$i]) != true) {
            print "<br><font color=#7d7d7d>".$plAlbum['1'][$i];
            if (empty($plDate['1'][$i]) != true) {
                print " (".$plDate['1'][$i].")";
            }
            print "</font>";
        }
    print ' 
        </td>
        <td style="width: 20px; border-collapse: collapse;">';
    // Livestreams and podcasts have no time length, check to suppress badge
    if ( $plTime['1'][$i] > 0 && $plTime['1'][$i] < 3600 ) {
        print '<span class="badge" style="float: right; margin: 3px!important;">'.date("i:s",$plTime['1'][$i]).'</span>';
    } elseif ( $plTime['1'][$i] > 0 ) {
        print '<span class="badge" style="float: right; margin: 3px!important;">'.date("H:i:s",$plTime['1'][$i]).'</span>';
    }
    print'
        </td>
    </tr>
    ';
    $i++;    
}
print '</table>';
/*
$i=0;
foreach($plFile[1] AS $file) {
    print '
    <li class="list-group-item">
        <div class="row">
            <div class="col-xs-1" style="width:8.3333333%;">
                <a href="?playpos='.$i.'" class="btn btn-success"><i class="mdi mdi-play" aria-hidden="true"></i></a>
            </div>
            <div class="col-xs-7" style="width:81.6666667%; margin-left: 20px; margin-right: -20px;">';
    if(trim($plTitle['1'][$i]) != "") {
        print '
                <strong>'.$plTitle['1'][$i].'</strong>';
    } else {
        print '
                <strong>'.basename($file).'</strong>';
    }
    print '
                <br><i>'.str_replace(";", " and ", $plArtist['1'][$i]).'</i>';
                if (empty($plAlbum['1'][$i]) != true) {
                    print "<br><font color=#7d7d7d>".$plAlbum['1'][$i];
                    if (empty($plDate['1'][$i]) != true) {
                        print " (".$plDate['1'][$i].")";
                    }
                    print "</font>";
                }
            print '
            </div>
            <div class="col-xs-4" style="width:10%;">';
                // Livestreams and podcasts have no time length, check to suppress badge
                if ( $plTime['1'][$i] > 0 && $plTime['1'][$i] < 3600 ) {
                    print '<span class="badge" style="float: right">'.date("i:s",$plTime['1'][$i]).'</span>';
                } elseif ( $plTime['1'][$i] > 0 ) {
                    print '<span class="badge" style="float: right">'.date("H:i:s",$plTime['1'][$i]).'</span>';
                }
            print'
            </div>
        </div>
    </li>
    ';
    $i++;    
}
*/
?>