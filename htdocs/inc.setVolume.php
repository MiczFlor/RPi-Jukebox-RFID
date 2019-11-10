<!--
Volume Select Form
-->
        <!-- input-group -->
        <?php
        $maxvalueselect = round(($maxvolumevalue/5))*5;
        ?>
        <div class="col-md-4 col-sm-6">
            <div class="row" style="margin-bottom:1em;">
              <div class="col-xs-6">
              <h4><?php print $lang['globalVolume']; ?></h4>
                <form name='volume' method='post' onsubmit='return setVolume();'>
                  <div class="input-group my-group">
                    <select id="volume" initialized="false" name="volume" class="selectpicker form-control">
                    <?php
                    for ($i = $maxvalueselect; $i >= 0; $i -= 5) {
                        print "<option value='{$i}'>{$i}%</option>";
                    }
                    ?>
                    </select>
                    <span class="input-group-btn">
                        <input type='submit' class="btn btn-default" name='submit' value='<?php print $lang['globalSet']; ?>'/>
                    </span>
                  </div>
                </form>
              </div>

                <div id="controlVolume">
                    <div class="col-xs-6">
                        <div id="volumeCircle" class="c100">
                        <span id="volumeValue"></span>
                            <div class="slice">
                                <div class="bar"></div>
                                <div class="fill"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <script>

                    function setVolume() {
                        $.ajax({
                            url: 'api/volume.php',
                            method: 'PUT',
                            data: $('#volume').children('option:selected').val()
                        }).success((data) => {
                            displayVolume(data);
                        });
                        return false;
                    }

                    function volumeChanged(volume) {
                        displayVolume(volume, false);
                    }

                    function displayVolume(volume, initialRequest) {
                        if ($('#volume').attr('initialized') === 'false') {
                            $('#volume').val(Math.round(volume/5) * 5);
                            $('#volume').attr('initialized', 'true');
                        }
                        $('#volumeValue').html(volume);
                        $('#volumeCircle').attr('class', `c100 p${volume}`);
                    }

                    $(document).ready(() => {
                        JUKEBOX.volumeChangedListener.push(volumeChanged);
                    });

                </script>
            </div><!-- ./row -->
        </div>
        <!-- /input-group -->
