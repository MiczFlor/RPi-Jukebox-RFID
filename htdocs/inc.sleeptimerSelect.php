<div class="row">
	<div class="col-xs-3">
		<div class="form-group">
		<form name='shutdownafter' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
			<select name='shutdownafter' id="sel5" class="form-control">
				<option value='0'>Unset sleep timer</option>
				<option value='5'>5 min</option>
				<option value='10'>10 min</option>
				<option value='15'>15 min</option>
				<option value='30'>30 min</option>
				<option value='60'>60 min</option>
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
			$sleeptimervalue = exec("sudo atq -q s | awk '{print $5}'");
			if ($sleeptimervalue != "") {
				$remainingsleeptimer = (strtotime($sleeptimervalue)-time())/60;
				print '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="'.$remainingsleeptimer.'" aria-valuemin="0" aria-valuemax="60" style="width:'.($remainingsleeptimer*100/60).'%">';
				print round($remainingsleeptimer)." min";
			}
			else {
				print '<div class="progress-bar progress-bar-success" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width:100%">';
	    			print "No sleep timer set";
			}
			?>
			</div><!-- / .progress-bar -->
  		</div><!-- / .progress -->
	</div><!-- / .col-xs-7 -->
</div><!-- / .row -->
