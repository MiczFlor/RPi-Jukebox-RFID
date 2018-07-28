<?php
// get current volume and set the volumeset array
	$volumevalue = exec("/usr/bin/sudo ".$conf['scripts_abs']."/playout_controls.sh -c=getvolume");
	$volumesteps = array(0,30,50,75,80,85,90,95,100);
?>
<div class="row">
	<div class="col-xs-3">
		<div class="form-group">
		<form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
			<select name='volume' id="sel1" class="form-control">
				<?php
					// for each volumestep
					for ($i=0;$i<count($volumesteps); $i++)
					{
						// if the last step is reached
						if($volumevalue == 100 && $volumesteps[$i] == 100){print "<option value='100' selected='selected'>100%</option>"; break;}
						// change the text on value 0 
						if($volumesteps[$i] == 0){$volumestep = "Mute (0%)";}
						else {$volumestep = $volumesteps[$i]."%";}
						// check if item fits the actual value
						if($volumevalue >= $volumesteps[$i] && $volumevalue < $volumesteps[$i+1] )
						{
							print "<option value='".$volumesteps[$i]."' selected='selected'>".$volumestep."</option>";
						}
						else
						{
							print "<option value='".$volumesteps[$i]."'>".$volumestep."</option>";
						}
					}		
				?>
			</select>
		</div><!-- / .form-group -->
	</div><!-- / .col-xs-3 -->
				<div class="col-xs-2">
					<input type='submit' class="btn btn-primary" name='submit' value='Set'/>
				</div><!-- / .col-xs-2 -->
		</form>

	<div class="col-xs-7">
		<div class="progress">
			<?php
			if ($volumevalue == 0) {
				print '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width:100%">';
    				print 'Muted (0%)';
			}
			else {
				print '<div class="progress-bar progress-bar-info" role="progressbar" aria-valuenow="'.$volumevalue.'" aria-valuemin="0" aria-valuemax="100" style="width:'.$volumevalue.'%">';
	    			print $volumevalue.'%';
			}
			?>
			</div><!-- / .progress-bar -->
  		</div><!-- / .progress -->
	</div><!-- / .col-xs-7 -->
</div><!-- / .row -->
