


<?php
/*
<div class="collapse" id="collapsePlaylist" aria-expanded="false" style="height: 0px;"> 
<table class="table table-striped table-hover table-condensed"> 
    <!--thead> 
        <tr> 
            <th></th> 
        </tr> 
    </thead--> 
    <tbody style="a {color:black;}; a:hover {color:white;}"> 
        <tr> 
            <td><a href="?playpos='.$i.'" class="btn btn-success btn-xs"><i class="mdi mdi-play" aria-hidden="true"></i></a></td> 
            <th scope=row>1</th> 
            <td>The title of the track - it could be long</td> 
            <td>03:12</td> 
        </tr>  
        <tr> 
            <td><a href="?playpos='.$i.'" class="btn btn-xs" style="color:black;"><i class="mdi mdi-play" aria-hidden="true"></i></a></td>  
            <th scope=row>2</th> 
            <td class="text">
                <span>
                This is the tenth album by 
                This is the tenth album by 
                This is the tenth album by 
                This is the tenth album by 
                This is the tenth album by 
                This is the tenth album by 
                This is the tenth album by 
                This is the tenth album by 
                </span>
            </td> 
            <td>23:42</td> 
        </tr>  
    </tbody> 
</table>
</div> 

*/
?>
<script>
$(document).ready(function() {
	$('#infoWrapper').load('ajax.loadInfo.php');
	$('#timeWrapper').load('ajax.loadTime.php');
	$('#overalltimeWrapper').load('ajax.loadOverallTime.php');
	var refreshId = setInterval(function() {
		$('#infoWrapper').load('ajax.loadInfo.php?' + 1*new Date());
		$('#timeWrapper').load('ajax.loadTime.php?' + 1*new Date());
		$('#overalltimeWrapper').load('ajax.loadOverallTime.php?' + 1*new Date());
	}, 1000);
});
</script>
<?php
print '
        <div class="panel-group">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h4 class="panel-title">
                        <div class="row" style="margin-bottom:1em;">
                            <div class="col-xs-1">
                                <i class="mdi mdi-'. $playerStatus['state'] .'"></i>
                            </div>
                            <div class="col-xs-7" id="infoWrapper"></div> 
                            <div class="col-xs-4">
                                <span class="badge">
									<div id="timeWrapper"></div>
								</span>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-xs-1">
                                <i class="mdi mdi-playlist-play"></i>
                            </div>
                            <div class="col-xs-7">
                                <a data-toggle="collapse" href="#collapse1" class="panel-title">Show playlist</a>
                            </div>
                            <div class="col-xs-4" id="overalltimeWrapper"></div>
                        </div>
                    </h4>
                </div>
                <div id="collapse1" class="panel-collapse collapse">
                    <ul class="list-group">
                    ';
                    $i=0;
                    foreach($plFile[1] AS $file) {
                        print '
                        <li class="list-group-item">
                            <div class="row">
                                <div class="col-xs-1">
                                    <a href="?playpos='.$i.'" class="btn btn-success"><i class="mdi mdi-play" aria-hidden="true"></i></a>
                                </div>
                                <div class="col-xs-7">
                                    <strong>'.$plTitle['1'][$i].'</strong>
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
                                <div class="col-xs-4">';
                                    // Livestreams and podcasts have no time length, check to suppress badge
                                    if ( $plTime['1'][$i] > 0 && $plTime['1'][$i] < 3600 ) {
                                        print '<span class="badge">'.date("i:s",$plTime['1'][$i]).'</span>';
                                    } elseif ( $plTime['1'][$i] > 0 ) {
                                        print '<span class="badge">'.date("H:i:s",$plTime['1'][$i]).'</span>';
                                    }
                                print'
                                </div>
                            </div>
                        </li>
                        ';
                        $i++;	
                    }
                    print '
                    </ul>
                </div>
            </div>
        </div>
';
?>
