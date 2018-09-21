


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
                            <div class="col-xs-8 col-md-9">
                                '.$playerStatus['file'].'
                            </div> 
                            <div class="col-xs-2">
                                <span class="badge">'.date("i:s",$playerStatus['elapsed']);
                                // Livestream and podcasts have no time length, show only elapsed time
                                if ( $plTime['1'][$playerStatus['pos']] > 0 ) {
                                    print ' / '.date("i:s",$plTime['1'][$playerStatus['pos']]);
                                }
                                print '</span>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-xs-1">
                                <i class="mdi mdi-playlist-play"></i>
                            </div>
                            <div class="col-xs-8 col-md-9">
                                <a data-toggle="collapse" href="#collapse1" class="panel-title">Show playlist</a>
                            </div>
                            <div class="col-xs-2">';
                                // Livestream and podcasts have no time length, check to suppress badge
                                if ( $playlistOverallTime > 0 ) {
                                    print '<span class="badge">'.date("i:s",$playlistPlayedTime).' / '.date("i:s",$playlistOverallTime).'</span>';
                                }
                            print '
                            </div>
                        </div>
                    </h4>
                </div>
                <div id="collapse1" class="panel-collapse collapse">
                    <ul class="list-group">
                    ';
                    $i=0;
                    foreach($plFile[1] AS $trackname) {
                        print '
                        <li class="list-group-item">
                            <div class="row">
                                <div class="col-xs-2 col-md-1">
                                    <a href="?playpos='.$i.'" class="btn btn-success"><i class="mdi mdi-play" aria-hidden="true"></i></a>
                                </div>
                                <div class="col-xs-8 col-md-9">
                                    '.$trackname.'
                                </div>
                                <div class="col-xs-2">';
                                    // Livestreams and podcasts have no time length, check to suppress badge
                                    if ( $plTime['1'][$i] > 0 ) {
                                        print '<span class="badge">'.date("i:s",$plTime['1'][$i]).'</span>';
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
