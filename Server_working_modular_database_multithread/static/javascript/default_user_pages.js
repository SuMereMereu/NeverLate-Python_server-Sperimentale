$(document).ready(function()
{
	$("#firstp_sidebar").click(function()
	{
		$("#firstp").removeClass()
		$("#settings").removeClass()
		$("#calendar").removeClass()
		
		$("#settings").addClass("hidden")
		$("#calendar").addClass("hidden")
	})
	
	$("#settings_sidebar").click(function()
	{
		$("#firstp").removeClass()
		$("#settings").removeClass()
		$("#calendar").removeClass()
		
		$("#firstp").addClass("hidden")
		$("#calendar").addClass("hidden")
	})
	
	$("#calendar_sidebar").click(function()
	{
		$("#firstp").removeClass()
		$("#settings").removeClass()
		$("#calendar").removeClass()
		
		$("#firstp").addClass("hidden")
		$("#settings").addClass("hidden")
	})
	
	$("#firstp_nav").click(function()
	{
		$("#firstp").removeClass()
		$("#settings").removeClass()
		$("#calendar").removeClass()
		
		$("#settings").addClass("hidden")
		$("#calendar").addClass("hidden")
		
		$("#firstp_nav").removeClass()
		$("#settings_nav").removeClass()
		$("#calendar_nav").removeClass()
		
		$("#firstp_nav").addClass("active")
	})
	
	$("#settings_nav").click(function()
	{
		$("#firstp").removeClass()
		$("#settings").removeClass()
		$("#calendar").removeClass()
		
		$("#firstp").addClass("hidden")
		$("#calendar").addClass("hidden")
		
		$("#firstp_nav").removeClass()
		$("#settings_nav").removeClass()
		$("#calendar_nav").removeClass()
		
		$("#settings_nav").addClass("active")
	})
	
	$("#calendar_nav").click(function()
	{
		$("#firstp").removeClass()
		$("#settings").removeClass()
		$("#calendar").removeClass()
		
		$("#firstp").addClass("hidden")
		$("#settings").addClass("hidden")
		
		$("#firstp_nav").removeClass()
		$("#settings_nav").removeClass()
		$("#calendar_nav").removeClass()
		
		$("#calendar_nav").addClass("active")
	})
	
})