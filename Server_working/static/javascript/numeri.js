$(document).ready(function()
{
	$('#minus').click(function()
	{
		delay=$('#delay').val();
		delay=delay-1;
		$('#delay').val(delay);
	})
	
	$('#more').click(function()
	{
		delay=parseInt($('#delay').val(), 10);
		delay=delay+1;
		$('#delay').val(delay);
	})
})