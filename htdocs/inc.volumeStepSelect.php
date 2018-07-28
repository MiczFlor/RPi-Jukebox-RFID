<?php
// get current volumestep and set the volumeset array
			$volstepvalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getvolstep");
			$volumesteps = array(1,2,3,5,7,10,15,20,0);
?>
<div class="row">
	<div class="col-xs-3">
		<div class="form-group">
		<form name='volstep' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
			<select name='volstep' id="sel3" class="form-control">
			<?php
					// for each volumestep
					foreach ($volumesteps as $volstep)
					{
						// change the text on value 0 
						if($volstep == 0){$step = "0% (up/down disabled)";}
						else {$step = $volstep."%";}
						// check if item fits the actual value
						if($volstep == $volstepvalue )
						{
							print "<option value='".$volstep."' selected='selected'>".$step."</option>";
						}
						else
						{
							print "<option value='".$volstep."'>".$step."</option>";
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
