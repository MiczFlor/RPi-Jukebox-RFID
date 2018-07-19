<div class="row">
	<div class="col-xs-3">
		<div class="form-group">
		<form name='volstep' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
			<select name='volstep' id="sel3" class="form-control">
				<option value='1'>1%</option>
				<option value='2'>2%</option>
				<option value='3'>3%</option>
				<option value='5'>5%</option>
				<option value='7'>7%</option>
				<option value='10'>10%</option>
				<option value='15'>15%</option>
				<option value='20'>20%</option>
				<option value='0'>0% (up/down disabled)</option>
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
			$volstepvalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getvolstep");
			if ($volstepvalue == 0) {
				print '<div class="progress-bar progress-bar progress-bar-danger" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width:100%">';
    				print 'Volume up/down disabled (0%)';
			}
			else {
				print '<div class="progress-bar progress-bar progress-bar-info" role="progressbar" aria-valuenow="'.$volstepvalue.'" aria-valuemin="0" aria-valuemax="100" style="width:'.$volstepvalue.'%">';
	    			print $volstepvalue.'%';
			}
			?>
			</div><!-- /.progress-bar -->
  		</div><!-- /.progress -->
	</div><!-- /.col-xs-7 -->
</div><!-- /.row -->
