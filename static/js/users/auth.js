$(function () {
  let $username = $('#user_name');  // 选择id为user_name的网页元素，需要定义一个id为user_name
  let $img = $(".form-item .captcha-graph-img img");  // 获取图像标签
  let sImageCodeId = "";  // 定义图像验证码ID值
  let $mobile = $('#mobile');  // 选择id为mobile的网页元素，需要定义一个id为mobile

  // 1、图像验证码逻辑
  generateImageCode();  // 生成图像验证码图片
  $img.click(generateImageCode);  // 点击图片验证码生成新的图片验证码图片


  // 判断用户是否注册
  // 2、用户名验证逻辑
  $username.blur(function () {
    fn_check_usrname();
  });

  // 3、手机号验证逻辑
  // 判断用户手机号是否注册
  $mobile.blur(function () {
    fn_check_mobile();
  });


  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
  function generateImageCode() {
    // 1、生成一个图片验证码随机编号
    sImageCodeId = generateUUID();
    // 2、拼接请求url /image_codes/<uuid:image_code_id>/
    let imageCodeUrl = "/image_codes/" + sImageCodeId + "/";
    // 3、修改验证码图片src地址
    $img.attr('src', imageCodeUrl)

  }

  // 生成图片UUID验证码
  function generateUUID() {
    let d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
      d += performance.now(); //use high-precision timer if available
    }
    let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      let r = (d + Math.random() * 16) % 16 | 0;
      d = Math.floor(d / 16);
      return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
  }

  // 判断用户名是否已经注册
  function fn_check_usrname() {
    let sUsername = $username.val();  // 获取用户名字符串
    if (sUsername === "") {
      message.showError('用户名不能为空！');
      return
    }
    // test()方法 判断字符串中是否匹配到正则表达式内容，返回的是boolean值 ( true / false )
    if (!(/^\w{5,20}$/).test(sUsername)) {
      message.showError('请输入5-20个字符的用户名');
      return
    }

    // 发送ajax请求，去后端查询用户名是否存在
    $.ajax({
      url: '/usernames/' + sUsername + '/',
      type: 'GET',
      dataType: 'json',
      // data:{'code':300268}
    })
      .done(function (res) {
        if (res.data.count !== 0) {
          message.showError(res.data.username + '已注册，请重新输入！')
        } else {
          message.showInfo(res.data.username + '能正常使用！')
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });
  }

  function fn_check_mobile() {
    let sMobile = $mobile.val();  // 获取用户输入的手机号码字符串
    let SreturnValue = "";
    if (sMobile === "") {
      message.showError('手机号不能为空！');
      return
    }
    if (!(/^1[345789]\d{9}$/).test(sMobile)) {
      message.showError('手机号码格式不正确，请重新输入！');
      return
    }

    $.ajax({
      url: '/mobiles/' + sMobile + '/',
      type: 'GET',
      dataType: 'json',
      async: false	// 把async关掉
    })
      .done(function (res) {
        if (res.data.count !== 0) {
          message.showError(res.data.mobile + '已注册，请重新输入！');
          SreturnValue = ""
        } else {
          message.showSuccess(res.data.mobile + '能正常使用!');
          SreturnValue = "success"

        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
        SreturnValue = ""
      });
    return SreturnValue

  }

});