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
	}, 3000);
});
</script>
<script>
$(document).ready(function() {
	$('#loadPlaylist').load('ajax.loadPlaylist.php');
	var refreshId = setInterval(function() {
		$('#loadPlaylist').load('ajax.loadPlaylist.php?' + 1*new Date());
	}, 3000);
});
</script>
<?php
print '
<table style="margin-bottom: 20px; width: 100%; border-collapse: collapse; border-top: 1px solid #444; border-bottom: 1px solid #444">
    <tr>
        <td style="padding: 10px 0; border-collapse: collapse;"><i class="mdi mdi-'. $playerStatus['state'] .'"></i> <span id="infoWrapper"></span></td>
        <td style="padding: 10px 0;width: 50px; border-collapse: collapse;"><div id="timeWrapper"></div></td>
    </tr>
    <tr>
        <td style="padding: 10px 0;border-collapse: collapse;"><i class="mdi mdi-playlist-play"></i> <a data-toggle="collapse" href="#collapse1" class="panel-title">Show playlist</a></td>
        <td style="padding: 10px 0;width: 50px; border-collapse: collapse;"><div id="overalltimeWrapper"></div></td>
    </tr>
</table>
<div id="collapse1" class="panel-collapse collapse" style="margin-bottom: 40px;">
    <ul class="list-group">
		<div id="loadPlaylist"></div>
    </ul>
</div>
';

/*
print '
        <div class="panel-group">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h4 class="panel-title">
                        <div class="row" style="margin-bottom:1em;">
                            <div class="col-xs-1" style="width:8.3333333%;">
                                <i class="mdi mdi-'. $playerStatus['state'] .'"></i>
                            </div>
                            <div class="col-xs-7" style="width:81.6666667%; margin-left: 20px; margin-right: -20px;" id="infoWrapper"></div> 
                            <div class="col-xs-4" style="width:10%;">
                                <span class="badge" style="float: right">
									<div id="timeWrapper"></div>
								</span>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-xs-1" style="width:8.3333333%;">
                                <i class="mdi mdi-playlist-play"></i>
                            </div>
                            <div class="col-xs-7" style="width:81.6666667%; margin-left: 20px; margin-right: -20px;">
                                <a data-toggle="collapse" href="#collapse1" class="panel-title">Show playlist</a>
                            </div>
                            <div class="col-xs-4" style="width:10%;" id="overalltimeWrapper"></div>
                        </div>
                    </h4>
                </div>
                <div id="collapse1" class="panel-collapse collapse">
                    <ul class="list-group">
						<div id="loadPlaylist"></div>
                    </ul>
                </div>
            </div>
        </div>
';
*/
?>
