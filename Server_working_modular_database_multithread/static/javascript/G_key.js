$(document).ready(
{
	var flag=parseInt(0, 10);

	$('#change').click(function()
	{
		alert ("prova")
		if (flag == 0)
		{
			alert("funzione");
			$('#G_key').removeAttr('readonly');
			flag=1;
		}
		
	}
	
	$('#alert_link').click(function()
	{
		alert("prova");	
	})
})