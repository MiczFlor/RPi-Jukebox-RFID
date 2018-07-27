<?php
// get current maxvolumevalue
	$maxvolumevalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getmaxvolume");
?>

<div class="row">
	<div class="col-xs-3">
		<div class="form-group">
		<form name='maxvolume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
			<select name='maxvolume' id="sel2" class="form-control">
			<?php   // make 10 steps from 100 to 0
					for ($i=100;$i>=0; $i-=10)
					{
						// change the text on value 0 
						if($i == 0){$step = "Mute (0%)";}
						else {$step = $i."%";}
						// check if item fits the actual value
						if($maxvolumevalue == $i )
						{
							print "<option value='".$i."' selected='selected'>".$step."</option>";
						}
						else
						{
							print "<option value='".$i."'>".$step."</option>";
						}
					}		
			?>
			</select>
		</div><!-- /.form-group -->
	</div><!-- /.col-xs-3 -->
				<div class="col-xs-2">
					<input type='submit' class="btn btn-primary" name='submit' value='Set'/>
				</div><!-- /.col-xs-2 -->
		</form>

	<div class="col-xs-7">
		<div class="progress">
			<?php
			if ($maxvolumevalue == 0) {
				print '<div class="progress-bar progress-bar progress-bar-danger" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width:100%">';
    				print 'Muted (0%)';
			}
			else {
				print '<div class="progress-bar progress-bar progress-bar-info" role="progressbar" aria-valuenow="'.$maxvolumevalue.'" aria-valuemin="0" aria-valuemax="100" style="width:'.$maxvolumevalue.'%">';
	    			print $maxvolumevalue.'%';
			}
			?>
			</div><!-- /.progress-bar -->
  		</div><!-- /.progress -->
	</div><!-- /.col-xs-7 -->
</div><!-- /.row -->
