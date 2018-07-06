<div class="row">
	<div class="col-xs-3">
		<div class="form-group">
		<form name='maxvolume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
			<select name='maxvolume' id="sel2" class="form-control">
				<option value='100'>100%</option>
				<option value='90'>90%</option>
				<option value='80'>80%</option>
				<option value='70'>70%</option>
				<option value='60'>60%</option>
				<option value='50'>50%</option>
				<option value='40'>40%</option>
				<option value='30'>30%</option>
				<option value='20'>20%</option>
				<option value='10'>10%</option>
				<option value='0'>Mute (0%)</option>
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
			$maxvolumevalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getmaxvolume");
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
